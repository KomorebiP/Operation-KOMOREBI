#!/usr/bin/env python3
"""Select untouched RRCT v0.50 holdout seeds from a public commitment string."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

COMMITMENT = (
    "RRCT-v0.50-synergistic-ephemeral-workspace-frozen-holdout-"
    "2026-08-24-no-outcome-inspection"
)
DEVELOPMENT_SEEDS = {50001, 50007, 50011}
SEED_COUNT = 4


def derive_seeds() -> list[int]:
    seeds: list[int] = []
    counter = 0
    while len(seeds) < SEED_COUNT:
        payload = f"{COMMITMENT}:{counter}".encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        for offset in range(0, len(digest), 4):
            value = int.from_bytes(digest[offset : offset + 4], "big")
            candidate = 100_000_000 + value % 900_000_000
            if candidate not in DEVELOPMENT_SEEDS and candidate not in seeds:
                seeds.append(candidate)
                if len(seeds) == SEED_COUNT:
                    break
        counter += 1
    return seeds


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    selected = derive_seeds()
    payload = {
        "schema": "rrct.v050.holdout_seed_selection.v1",
        "version": "0.50.0.dev1",
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "commitment": COMMITMENT,
        "commitment_sha256": hashlib.sha256(COMMITMENT.encode("utf-8")).hexdigest(),
        "development_seeds": sorted(DEVELOPMENT_SEEDS),
        "selected_seeds": selected,
        "seed_count": SEED_COUNT,
        "candidate_outcomes_examined": False,
        "postoutcome_seed_replacement_permitted": False,
    }
    unsigned = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
    path = root / "validation/V0_50_HOLDOUT_SEED_SELECTION.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    companion = path.with_suffix(path.suffix + ".sha256")
    companion.write_text(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
