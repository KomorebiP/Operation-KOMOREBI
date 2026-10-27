#!/usr/bin/env python3
"""Select v0.46 holdout seeds without evaluating candidate outcomes."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

NAMESPACE = b"RRCT-v0.46-neutral-self-indexed-workspace-holdout-v1"
EXPOSED = {46011, 46012, 46013, 46014}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "validation/V0_46_HOLDOUT_SEED_SELECTION.json"
    if output.exists():
        raise RuntimeError("v0.46 holdout seed receipt already exists")
    candidates: list[int] = []
    counter = 0
    while len(candidates) < 64:
        block = hashlib.sha256(NAMESPACE + counter.to_bytes(8, "big")).digest()
        for offset in range(0, len(block), 4):
            value = 100_000_000 + int.from_bytes(block[offset : offset + 4], "big") % 800_000_000
            if value not in EXPOSED and value not in candidates:
                candidates.append(value)
            if len(candidates) == 64:
                break
        counter += 1
    selected = candidates[:4]
    protocol = root / "validation/V0_46_NEUTRAL_SELF_INDEXED_WORKSPACE_PROTOCOL.md"
    payload = {
        "schema": "rrct.v046.holdout_seed_selection.v1",
        "version": "0.46.0.dev1",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "method": "SHA-256 expansion of a fixed namespace; first four unique nondevelopment seeds",
        "namespace_sha256": hashlib.sha256(NAMESPACE).hexdigest(),
        "protocol_sha256": sha256(protocol),
        "development_seeds_excluded": sorted(EXPOSED),
        "candidate_count": len(candidates),
        "candidate_pool_sha256": hashlib.sha256(
            json.dumps(candidates, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "holdout_seeds": selected,
        "candidate_outcomes_examined": False,
        "postoutcome_seed_replacement_prohibited": True,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{sha256(output)}  {output.name}\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
