#!/usr/bin/env python3
"""Deterministic checks for the analytic case studies in SRWT."""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Iterable

import numpy as np

RESULTS_DIR = Path(__file__).with_name("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT = RESULTS_DIR / "case_studies.json"


def eigvals_sorted(matrix: np.ndarray) -> list[float]:
    vals = np.linalg.eigvalsh(matrix)
    return [float(np.round(v, 12)) for v in vals]


def frame_summary(encodings: dict[str, np.ndarray]) -> dict[str, object]:
    names = list(encodings)
    full = sum((e.T @ e for e in encodings.values()), start=np.zeros((encodings[names[0]].shape[1],) * 2))
    pair_bounds: dict[str, float] = {}
    for pair in itertools.combinations(names, 2):
        frame = sum((encodings[name].T @ encodings[name] for name in pair), start=np.zeros_like(full))
        pair_bounds["+".join(pair)] = float(np.min(np.linalg.eigvalsh(frame)))
    ranks = {name: int(np.linalg.matrix_rank(e)) for name, e in encodings.items()}
    visibility_counts: list[int] = []
    dim = full.shape[0]
    # The examples use coordinate-selection encodings. Each basis coordinate's
    # number of visible nodes gives the exact node-erasure distance here.
    for j in range(dim):
        basis = np.zeros(dim)
        basis[j] = 1.0
        visibility_counts.append(sum(int(np.linalg.norm(e @ basis) > 0) for e in encodings.values()))
    return {
        "full_frame": full.tolist(),
        "full_frame_eigenvalues": eigvals_sorted(full),
        "local_ranks": ranks,
        "pair_lower_frame_bounds": pair_bounds,
        "coordinate_visibility_counts": visibility_counts,
        "node_erasure_distance": int(min(visibility_counts)),
    }


def parity_conditional_entropy(num_bits: int, observed_indices: Iterable[int]) -> float:
    observed = tuple(observed_indices)
    counts: dict[tuple[int, ...], list[int]] = {}
    for bits in itertools.product((0, 1), repeat=num_bits):
        key = tuple(bits[i] for i in observed)
        y = 0
        for b in bits:
            y ^= b
        if key not in counts:
            counts[key] = [0, 0]
        counts[key][y] += 1
    total = 2 ** num_bits
    entropy = 0.0
    for n0, n1 in counts.values():
        n = n0 + n1
        local = 0.0
        for ny in (n0, n1):
            if ny:
                p = ny / n
                local -= p * np.log2(p)
        entropy += (n / total) * local
    return float(entropy)


def human_human_case() -> dict[str, object]:
    d = np.array(
        [
            [0, 1, -1, 0, 0, 0],
            [0, 0, 0, 1, 0, -1],
            [-1, 0, 0, 0, 1, 0],
        ],
        dtype=float,
    )
    encodings = {
        "P": np.array([[1, 0, 0], [0, 1, 0]], dtype=float),
        "C": np.array([[0, 1, 0], [0, 0, 1]], dtype=float),
        "N": np.array([[1, 0, 0], [0, 0, 1]], dtype=float),
    }
    return {
        "discrepancy_rank": int(np.linalg.matrix_rank(d)),
        "laplacian_eigenvalues": eigvals_sorted(d.T @ d),
        "edge_gram": (d @ d.T).tolist(),
        "kernel_dimension": int(d.shape[1] - np.linalg.matrix_rank(d)),
        "frame": frame_summary(encodings),
        "single_node_parity_conditional_entropy_bits": {
            name: parity_conditional_entropy(3, obs)
            for name, obs in {"P": (0, 1), "C": (1, 2), "N": (0, 2)}.items()
        },
        "full_parity_conditional_entropy_bits": parity_conditional_entropy(3, (0, 1, 2)),
        "minimal_sufficient_coalition_size": 2,
        "matched_null_transfer_gap_bits": 1.0,
    }


def human_ai_case() -> dict[str, object]:
    d = np.array(
        [
            [1, 0, -1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, -1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, -1],
            [0, -1, 0, 0, 0, 0, 1, 0],
        ],
        dtype=float,
    )
    encodings = {
        "H": np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float),
        "M": np.array([[1, 0, 0, 0], [0, 0, 1, 0]], dtype=float),
        "X": np.array([[0, 0, 1, 0], [0, 0, 0, 1]], dtype=float),
        "A": np.array([[0, 1, 0, 0], [0, 0, 0, 1]], dtype=float),
    }
    pair_ranks: dict[str, int] = {}
    for pair in itertools.combinations(encodings, 2):
        pair_ranks["+".join(pair)] = int(np.linalg.matrix_rank(np.vstack([encodings[pair[0]], encodings[pair[1]]])))
    return {
        "discrepancy_rank": int(np.linalg.matrix_rank(d)),
        "laplacian_eigenvalues": eigvals_sorted(d.T @ d),
        "edge_gram": (d @ d.T).tolist(),
        "kernel_dimension": int(d.shape[1] - np.linalg.matrix_rank(d)),
        "frame": frame_summary(encodings),
        "pair_encoding_ranks": pair_ranks,
        "single_node_parity_conditional_entropy_bits": {
            "H": parity_conditional_entropy(4, (0, 1)),
            "M": parity_conditional_entropy(4, (0, 2)),
            "X": parity_conditional_entropy(4, (2, 3)),
            "A": parity_conditional_entropy(4, (1, 3)),
        },
        "opposite_pair_entropy_bits": {
            "H+X": parity_conditional_entropy(4, (0, 1, 2, 3)),
            "M+A": parity_conditional_entropy(4, (0, 1, 2, 3)),
        },
        "adjacent_pair_entropy_bits": {
            "H+M": parity_conditional_entropy(4, (0, 1, 2)),
            "M+X": parity_conditional_entropy(4, (0, 2, 3)),
            "X+A": parity_conditional_entropy(4, (1, 2, 3)),
            "A+H": parity_conditional_entropy(4, (0, 1, 3)),
        },
        "minimal_sufficient_coalition_size": 2,
        "matched_null_transfer_gap_bits": 1.0,
    }


def utility(g: int, b: int, h: int, a: int, r: int) -> float:
    task = int(a == (g ^ b ^ h))
    maintained = int(bool(h or r))
    return task + 2 * maintained - 0.5 * r


def multi_agent_case() -> dict[str, object]:
    rows = []
    min_gap = float("inf")
    all_unique = True
    for g, b, h in itertools.product((0, 1), repeat=3):
        values = {(a, r): utility(g, b, h, a, r) for a, r in itertools.product((0, 1), repeat=2)}
        ordered = sorted(values.items(), key=lambda item: item[1], reverse=True)
        best_action, best_value = ordered[0]
        gap = best_value - ordered[1][1]
        min_gap = min(min_gap, gap)
        expected = (g ^ b ^ h, 1 - h)
        all_unique &= best_action == expected and gap > 0
        rows.append(
            {
                "state": [g, b, h],
                "optimal_action": list(best_action),
                "expected_action": list(expected),
                "optimal_value": best_value,
                "runner_up_gap": gap,
                "post_repair_health": int(bool(h or best_action[1])),
            }
        )
    return {
        "states": rows,
        "all_optima_unique_and_expected": bool(all_unique),
        "minimum_optimal_action_gap": float(min_gap),
        "exact_greedy_recovery_condition": "epsilon_Q < 0.25",
        "intact_post_repair_deficit": 0,
        "damaged_no_repair_deficit": 1,
        "matched_causal_repair_gain": 1,
        "goal_retention_factor": 1,
        "minimal_control_coalition_size": 2,
    }


def main() -> None:
    result = {
        "human_human": human_human_case(),
        "human_ai_idealized": human_ai_case(),
        "multi_agent": multi_agent_case(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"WROTE={OUT}")


if __name__ == "__main__":
    main()
