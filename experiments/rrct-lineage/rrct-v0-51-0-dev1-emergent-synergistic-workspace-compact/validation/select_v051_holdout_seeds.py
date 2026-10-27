#!/usr/bin/env python3
"""Select fresh v0.51 holdout seeds without examining outcomes."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

DEVELOPMENT_SEEDS = [51001, 51007]
COUNT = 4
COMMITMENT = (
    "RRCT v0.51 emergent synergistic workspace | frozen holdout seed "
    "selection | no candidate outcomes examined | 2026-08-24"
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "validation/V0_51_HOLDOUT_SEED_SELECTION.json"
    companion = output.with_suffix(output.suffix + ".sha256")
    if output.exists() or companion.exists():
        raise RuntimeError("v0.51 holdout seed receipt already exists")
    selected: list[int] = []
    counter = 0
    while len(selected) < COUNT:
        digest = hashlib.sha256(f"{COMMITMENT}|{counter}".encode()).digest()
        for offset in range(0, len(digest), 4):
            value = int.from_bytes(digest[offset : offset + 4], "big")
            seed = 100_000_000 + value % 800_000_000
            if seed not in DEVELOPMENT_SEEDS and seed not in selected:
                selected.append(seed)
                if len(selected) == COUNT:
                    break
        counter += 1
    payload = {
        "schema": "rrct.v051.holdout_seed_selection.v1",
        "version": "0.51.0.dev1",
        "created_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "commitment": COMMITMENT,
        "commitment_sha256": hashlib.sha256(COMMITMENT.encode()).hexdigest(),
        "development_seeds": DEVELOPMENT_SEEDS,
        "selected_seeds": selected,
        "candidate_outcomes_examined": False,
        "post_selection_replacement_permitted": False,
    }
    unsigned = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(unsigned.encode()).hexdigest()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    file_sha = hashlib.sha256(output.read_bytes()).hexdigest()
    companion.write_text(f"{file_sha}  {output.name}\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
