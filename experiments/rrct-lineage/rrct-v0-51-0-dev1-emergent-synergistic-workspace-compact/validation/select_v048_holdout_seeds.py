#!/usr/bin/env python3
"""Select fresh RRCT v0.48 holdout seeds without evaluating outcomes."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

NAMESPACE = (
    "RRCT-v0.48-distributed-sparse-jspace-frozen-holdout-2026-08-24-v1"
)
CANDIDATE_COUNT = 128
SELECT_COUNT = 4
EXCLUDED = {
    48011,
    48012,
    48013,
    48014,
    48017,
    48023,
    48029,
    161625576,
    156878792,
    822521852,
    294523660,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_pool() -> list[int]:
    values: list[int] = []
    counter = 0
    while len(values) < CANDIDATE_COUNT:
        block = hashlib.sha256(f"{NAMESPACE}:{counter}".encode("utf-8")).digest()
        for start in range(0, len(block), 4):
            value = int.from_bytes(block[start : start + 4], "big")
            seed = 100_000_000 + value % 900_000_000
            if seed not in EXCLUDED and seed not in values:
                values.append(seed)
                if len(values) == CANDIDATE_COUNT:
                    break
        counter += 1
    return values


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    protocol = root / "validation/V0_48_DISTRIBUTED_SPARSE_JSPACE_PROTOCOL.md"
    output = root / "validation/V0_48_HOLDOUT_SEED_SELECTION.json"
    if output.exists():
        raise RuntimeError("v0.48 holdout seed receipt already exists")
    candidates = candidate_pool()
    candidate_bytes = json.dumps(candidates, separators=(",", ":")).encode("utf-8")
    payload = {
        "schema": "rrct.v048.holdout_seed_selection.v1",
        "version": "0.48.0.dev1",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "method": (
            "SHA-256 expansion of a fixed public namespace; first four unique "
            "nondevelopment seeds"
        ),
        "namespace": NAMESPACE,
        "namespace_sha256": hashlib.sha256(NAMESPACE.encode("utf-8")).hexdigest(),
        "protocol_sha256": sha256(protocol),
        "candidate_count": len(candidates),
        "candidate_pool_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
        "development_and_predecessor_seeds_excluded": sorted(EXCLUDED),
        "holdout_seeds": candidates[:SELECT_COUNT],
        "candidate_outcomes_examined": False,
        "postoutcome_seed_replacement_prohibited": True,
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    digest = sha256(output)
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
