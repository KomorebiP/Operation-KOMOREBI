#!/usr/bin/env python3
"""Generate the exact learned-output-free inputs for Neuralese v0.3.1.

Author: Komorebi P.

This utility may be run before the execution freeze.  It samples only D4
coordinate episodes and validates symbolic D4 words.  It never opens a learned
checkpoint and contains no learned-state, decoder, margin, or spectral query.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
EPISODE_SEEDS = {0: 940_000, 1: 941_000}
EPISODES_PER_CHECKPOINT = 8

# A nonempty recurrent representative for every abstract D4 endpoint.  The
# identity uses F^2 so no base state is an unadvanced entry anchor.
BASE_TRANSVERSAL = {
    "e": (1, 1),
    "R": (0,),
    "R2": (0, 0),
    "R3": (0, 0, 0),
    "F": (1,),
    "FR": (1, 0),
    "FR2": (1, 0, 0),
    "FR3": (1, 0, 0, 0),
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha256_without_field(value: dict[str, Any], field: str) -> str:
    stripped = {key: item for key, item in value.items() if key != field}
    return hashlib.sha256(canonical_json_bytes(stripped)).hexdigest()


def _load_core():
    sys.path.insert(0, str(ROOT))
    try:
        import core  # type: ignore
    finally:
        sys.path.pop(0)
    if Path(core.__file__).resolve().parent != ROOT:
        raise ImportError("core module did not resolve to the frozen package")
    return core


def _episode_record(batch: Any, episode: int) -> dict[str, Any]:
    maps = np.asarray(batch.maps[episode], dtype=np.int64)
    tables = np.asarray(batch.tables[episode], dtype=np.float32)
    mapping = np.asarray(batch.canonical_to_slot[episode], dtype=np.int64)
    phi = np.asarray(batch.phi[episode], dtype=np.int64)
    if mapping.shape != (2,) or set(mapping.tolist()) != {0, 1}:
        raise ArithmeticError("canonical_to_slot is not a permutation")
    if any(not np.array_equal(np.sort(row), np.arange(8)) for row in maps):
        raise ArithmeticError("sampled operator map is not a permutation")
    if not np.array_equal(tables, np.eye(8, dtype=np.float32)[maps]):
        raise ArithmeticError("sampled table and integer map disagree")
    return {
        "episode_index": int(episode),
        "phi": phi.tolist(),
        "canonical_to_slot": mapping.tolist(),
        "slot_maps": maps.tolist(),
        "tables": tables.astype(int).tolist(),
    }


def generate_inputs() -> dict[str, Any]:
    core = _load_core()
    canonical_maps = core.canonical_maps("d4")
    endpoint_actions: dict[str, list[int]] = {}
    actions_seen: set[tuple[int, ...]] = set()
    for name, word in BASE_TRANSVERSAL.items():
        if not word:
            raise ArithmeticError("base transversal contains an entry anchor")
        action = tuple(map(int, core.compose_maps(canonical_maps, word)))
        if action in actions_seen:
            raise ArithmeticError("base transversal does not cover distinct endpoints")
        actions_seen.add(action)
        endpoint_actions[name] = list(action)
    if len(actions_seen) != 8:
        raise ArithmeticError("base transversal does not cover all eight D4 elements")

    checkpoint_records: dict[str, Any] = {}
    for checkpoint_seed, episode_seed in EPISODE_SEEDS.items():
        rng = np.random.default_rng(episode_seed)
        batch = core.sample_batch(
            rng, EPISODES_PER_CHECKPOINT, 0, family="d4"
        )
        checkpoint_records[str(checkpoint_seed)] = {
            "checkpoint_seed": checkpoint_seed,
            "episode_seed": episode_seed,
            "episodes": [
                _episode_record(batch, episode)
                for episode in range(EPISODES_PER_CHECKPOINT)
            ],
        }

    value: dict[str, Any] = {
        "schema": "komorebi.neuralese.entry_cone_holonomy.frozen_inputs.v1",
        "version": "0.3.1",
        "author": "Komorebi P.",
        "scientific_status": "generated_without_learned_checkpoint_access",
        "generator_encoding": {"0": "R", "1": "F"},
        "episode_rule": {
            "episode_seeds": {str(k): v for k, v in EPISODE_SEEDS.items()},
            "episodes_per_checkpoint": EPISODES_PER_CHECKPOINT,
            "family": "d4",
            "sample_length": 0,
            "visible_starts": list(range(8)),
        },
        "base_transversal": {
            "purpose": (
                "one nonempty recurrent path for each abstract D4 endpoint; "
                "all eight visible starts are crossed with every path"
            ),
            "words": {name: list(word) for name, word in BASE_TRANSVERSAL.items()},
            "canonical_actions": endpoint_actions,
            "base_case_count_per_episode": 64,
        },
        "checkpoints": checkpoint_records,
    }
    value["content_sha256_without_this_field"] = sha256_without_field(
        value, "content_sha256_without_this_field"
    )
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).resolve().parent / "V031_FROZEN_INPUTS.json"
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite frozen input candidate: {output}")
    value = generate_inputs()
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"V031_FROZEN_INPUTS={output}")
    print(f"CONTENT_SHA256={value['content_sha256_without_this_field']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
