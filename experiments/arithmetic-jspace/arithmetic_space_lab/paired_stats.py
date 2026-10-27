from __future__ import annotations

import math
from typing import Any


def mcnemar_exact_two_sided(correct_only: int, shuffled_only: int) -> float:
    discordant = correct_only + shuffled_only
    if discordant == 0:
        return 1.0
    tail = min(correct_only, shuffled_only)
    log_terms = [
        math.lgamma(discordant + 1)
        - math.lgamma(index + 1)
        - math.lgamma(discordant - index + 1)
        - discordant * math.log(2.0)
        for index in range(tail + 1)
    ]
    maximum = max(log_terms)
    probability = 2.0 * math.exp(maximum) * sum(
        math.exp(value - maximum) for value in log_terms
    )
    return min(1.0, probability)


def paired_exact_group(
    items: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, Any]:
    total = len(items)
    correct_hits = sum(int(bool(correct["answer_exact_match"])) for correct, _ in items)
    shuffled_hits = sum(int(bool(shuffled["answer_exact_match"])) for _, shuffled in items)
    correct_only = sum(
        int(bool(correct["answer_exact_match"]) and not bool(shuffled["answer_exact_match"]))
        for correct, shuffled in items
    )
    shuffled_only = sum(
        int(bool(shuffled["answer_exact_match"]) and not bool(correct["answer_exact_match"]))
        for correct, shuffled in items
    )
    return {
        "examples": total,
        "correct_exact_count": correct_hits,
        "shuffled_exact_count": shuffled_hits,
        "correct_exact_rate": correct_hits / max(1, total),
        "shuffled_exact_rate": shuffled_hits / max(1, total),
        "rate_difference": (correct_hits - shuffled_hits) / max(1, total),
        "correct_only": correct_only,
        "shuffled_only": shuffled_only,
        "both_correct": sum(
            int(bool(correct["answer_exact_match"]) and bool(shuffled["answer_exact_match"]))
            for correct, shuffled in items
        ),
        "both_incorrect": sum(
            int(not bool(correct["answer_exact_match"]) and not bool(shuffled["answer_exact_match"]))
            for correct, shuffled in items
        ),
        "mcnemar_exact_two_sided_p": mcnemar_exact_two_sided(
            correct_only, shuffled_only
        ),
    }
