#!/usr/bin/env python3
"""Reproduce the inherited v0.2.1 exact-L6 / cumulative-H3 hard result."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from checkpoint_io import file_sha256, load_checkpoint
from core import sample_batch
from run_completion_surface import (
    ROOT,
    atomic_json,
    build_episode_tree,
    intern_hard_signatures,
    recursive_future_aggregates,
    summarize_cell,
)


OUTPUT = ROOT / "results" / "LINEAGE_REGRESSION.json"


def run_lineage_regression() -> dict[str, object]:
    preregistration = json.loads((ROOT / "PREREGISTRATION.json").read_text(encoding="utf-8"))
    seeds: dict[str, object] = {}
    all_passed = True
    for seed in (0, 1):
        filename = f"projective_terminal_seed{seed}.pt"
        checkpoint = load_checkpoint(
            ROOT / "checkpoints" / filename,
            preregistration["checkpoints"][filename],
        )
        # v0.2.1 drew 64 episodes, then used the first eight for this endpoint.
        batch = sample_batch(
            np.random.default_rng(910_000 + 1_000 * seed),
            64,
            0,
            family="d4",
        )
        episodes: list[dict[str, object]] = []
        correct = 0
        decisions = 0
        maximum_split = 0
        for episode in range(8):
            tree = build_episode_tree(
                checkpoint.weights,
                batch.tables[episode],
                batch.maps[episode],
                batch.canonical_to_slot[episode],
                9,
                episode_id=f"v0.2.1:seed{seed}:episode{episode}",
            )
            signatures = intern_hard_signatures(
                tree.predictions_by_depth,
                3,
                episode_id=tree.episode_id,
                episode_scope=tree.scope_token,
            )
            aggregates = recursive_future_aggregates(tree, 3)
            cell = summarize_cell(
                tree,
                signatures,
                aggregates,
                6,
                3,
                history_mode="exact",
                future_mode="cumulative",
            )
            episodes.append(
                {
                    "episode_index": episode,
                    "decision_count": cell["decision_count"],
                    "semantic_continuation_accuracy": cell[
                        "semantic_continuation_accuracy"
                    ],
                    "signature_class_count": cell["signature_class_count"],
                    "maximum_split_multiplicity": cell[
                        "maximum_split_multiplicity"
                    ],
                    "maximum_merge_multiplicity": cell[
                        "maximum_merge_multiplicity"
                    ],
                    "minimum_target_margin": cell["minimum_target_margin"],
                    "passed": cell["hard_completion_pass"],
                }
            )
            correct += int(cell["correct_decision_count"])
            decisions += int(cell["decision_count"])
            maximum_split = max(maximum_split, int(cell["maximum_split_multiplicity"]))
        seed_passed = bool(
            decisions == 61_440
            and correct == decisions
            and maximum_split == 1
            and all(bool(record["passed"]) for record in episodes)
        )
        all_passed &= seed_passed
        seeds[str(seed)] = {
            "episode_seed": 910_000 + 1_000 * seed,
            "sampled_batch_size": 64,
            "audited_first_episode_count": 8,
            "history_depth": 6,
            "future_horizon": 3,
            "history_mode": "exact",
            "future_mode": "cumulative",
            "decision_count": decisions,
            "correct_decision_count": correct,
            "semantic_continuation_accuracy": correct / decisions,
            "maximum_split_multiplicity": maximum_split,
            "episodes": episodes,
            "passed": seed_passed,
        }
    return {
        "schema": "komorebi.neuralese.v0.2.1.lineage_regression.v1",
        "purpose": "Reproduce the already-known v0.2.1 ordinary exact-L6/H3 hard endpoint; this is not a new v0.3.0 scientific result.",
        "expected_decisions_per_seed": 61_440,
        "expected_accuracy": 1.0,
        "expected_maximum_split_multiplicity": 1,
        "seeds": seeds,
        "passed": all_passed,
        "runner_sha256": file_sha256(Path(__file__).resolve()),
    }


def main() -> int:
    result = run_lineage_regression()
    atomic_json(OUTPUT, result)
    print(json.dumps({"output": str(OUTPUT), "passed": result["passed"]}, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
