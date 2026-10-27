from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
result_path = ROOT / "results" / "fake_fixture_audit.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
rows = result["rows"]

def arithmetic_mean(field: str) -> float:
    return sum(float(row[field]) for row in rows) / len(rows)

checks = {
    "necessity": arithmetic_mean("necessity_effect"),
    "order": arithmetic_mean("order_effect"),
    "structure": arithmetic_mean("structure_effect"),
    "procedure_transplant": arithmetic_mean("procedure_transplant_effect"),
    "twin_transplant": arithmetic_mean("twin_transplant_effect"),
}
for name, value in checks.items():
    stored = float(result["summary"][name]["mean"])
    if abs(value - stored) > 1e-12:
        raise SystemExit(f"Independent mean mismatch for {name}: {value} != {stored}")

if max(float(row["replay_max_abs"]) for row in rows) != float(result["summary"]["replay_max_abs"]):
    raise SystemExit("Replay maximum mismatch")
if result["summary"]["status"] != "PROCEDURE_SPECIFIC":
    raise SystemExit("Engineered positive control did not reach PROCEDURE_SPECIFIC")
if result.get("execution_boundary", {}).get("engineered_positive_control") is not True:
    raise SystemExit("Engineered result boundary is missing")
receipt = hashlib.sha256(
    json.dumps(checks, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
print("SRIC_REAL_LRM_PILOT_INDEPENDENT_VERIFY=PASS")
print(f"verification_receipt={receipt}")
