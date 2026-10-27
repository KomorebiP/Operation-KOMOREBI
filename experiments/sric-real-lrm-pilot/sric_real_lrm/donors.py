from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Sequence

from .dataset import jaccard_distance, signature_token_set
from .hashing import sha256_object
from .schemas import TaskRecord


@dataclass(frozen=True)
class DonorAssignment:
    recipient_id: str
    donor_id: str
    answer: str
    proof_depth: int
    signature_distance: float

    def to_mapping(self) -> dict[str, object]:
        return asdict(self)


def build_same_answer_far_proof_plan(records: Sequence[TaskRecord]) -> list[DonorAssignment]:
    buckets: dict[tuple[str, int], list[TaskRecord]] = defaultdict(list)
    for record in records:
        buckets[(record.answer.strip().lower(), record.proof_depth)].append(record)

    plan: list[DonorAssignment] = []
    for recipient in records:
        candidates = [
            x for x in buckets[(recipient.answer.strip().lower(), recipient.proof_depth)]
            if x.task_id != recipient.task_id and x.orbit_id != recipient.orbit_id
        ]
        if not candidates:
            candidates = [
                x for x in records
                if x.task_id != recipient.task_id
                and x.orbit_id != recipient.orbit_id
                and x.answer.strip().lower() == recipient.answer.strip().lower()
            ]
        if not candidates:
            raise ValueError(f"No same-answer donor for {recipient.task_id}")
        recipient_tokens = signature_token_set(recipient)
        ranked = sorted(
            (
                (jaccard_distance(recipient_tokens, signature_token_set(candidate)), candidate)
                for candidate in candidates
            ),
            key=lambda item: (-item[0], item[1].task_id),
        )
        distance, donor = ranked[0]
        plan.append(
            DonorAssignment(
                recipient_id=recipient.task_id,
                donor_id=donor.task_id,
                answer=recipient.answer,
                proof_depth=recipient.proof_depth,
                signature_distance=float(distance),
            )
        )
    return plan


def donor_plan_digest(plan: Sequence[DonorAssignment]) -> str:
    return sha256_object([x.to_mapping() for x in plan])


def validate_donor_plan(records: Sequence[TaskRecord], plan: Sequence[DonorAssignment]) -> None:
    by_id = {r.task_id: r for r in records}
    if {p.recipient_id for p in plan} != set(by_id):
        raise ValueError("Donor plan must cover every task exactly once")
    for assignment in plan:
        recipient = by_id[assignment.recipient_id]
        donor = by_id[assignment.donor_id]
        if recipient.task_id == donor.task_id:
            raise ValueError("Self-donor detected")
        if recipient.orbit_id == donor.orbit_id:
            raise ValueError("Semantic twin selected as procedure donor")
        if recipient.answer.strip().lower() != donor.answer.strip().lower():
            raise ValueError("Procedure donor has a different answer")
