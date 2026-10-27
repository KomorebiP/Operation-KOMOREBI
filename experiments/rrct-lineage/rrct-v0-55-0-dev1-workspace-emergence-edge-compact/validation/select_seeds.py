from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def expand(namespace: str, count: int) -> list[int]:
    values: list[int] = []
    index = 0
    while len(values) < count:
        digest = hashlib.sha256(f"{namespace}:{index}".encode()).digest()
        value = int.from_bytes(digest[:8], "big") % 900_000_000 + 100_000_000
        if value not in values:
            values.append(value)
        index += 1
    return values

payload = {
    "schema": "rrct.v055.edge_seed_selection.v1",
    "namespace": "RRCT-v0.55-workspace-edge-primary-2026-08-25",
    "primary_base_seeds": expand("RRCT-v0.55-workspace-edge-primary-2026-08-25", 24),
    "cross_initialization_seeds": expand("RRCT-v0.55-edge-cross-init-2026-08-25", 8),
    "cross_data_seeds": expand("RRCT-v0.55-edge-cross-data-2026-08-25", 4),
    "selection_uses_model_outcomes": False,
}
(ROOT / "validation/SEEDS.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, indent=2, sort_keys=True))
