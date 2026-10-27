from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np

from sric_real_lrm.receipts import load_and_verify_result

ROOT = Path(__file__).resolve().parent
result_path = ROOT / "results" / "fake_fixture_block24.json"
result = load_and_verify_result(result_path)
causal = result["causal_admission"]
summary = causal["summary"]
rows = causal["rows"]


def arithmetic_mean(field: str) -> float:
    values = [float(row[field]) for row in rows if row[field] is not None]
    return sum(values) / len(values)


field_map = {
    "necessity": "necessity_effect",
    "order": "order_effect",
    "norm_structure": "norm_structure_effect",
    "covariance_structure": "covariance_structure_effect",
    "procedure_transplant": "procedure_transplant_effect",
    "different_answer_transplant": "different_answer_transplant_effect",
    "twin_transplant": "twin_transplant_effect",
}
checks = {}
for summary_name, row_field in field_map.items():
    value = arithmetic_mean(row_field)
    stored = float(summary[summary_name]["mean"])
    if abs(value - stored) > 1e-12:
        raise SystemExit(f"Independent mean mismatch for {summary_name}: {value} != {stored}")
    checks[summary_name] = value

if max(float(row["replay_max_abs"]) for row in rows) != float(summary["replay_max_abs"]):
    raise SystemExit("Replay maximum mismatch")
if summary["status"] != "CONTENT_SPECIFIC":
    raise SystemExit("Engineered causal admission did not reach CONTENT_SPECIFIC")
if result["overall_status"] != "CAUSALLY_VALIDATED":
    raise SystemExit("Engineered pipeline did not reach CAUSALLY_VALIDATED")
if result.get("execution_boundary", {}).get("engineered_positive_control") is not True:
    raise SystemExit("Engineered result boundary is missing")

semantic = result["semantic_escalation"]
basis = np.asarray(semantic["selected"]["basis"], dtype=np.float64)
orthogonality = float(np.max(np.abs(basis.T @ basis - np.eye(basis.shape[1]))))
if orthogonality > 1e-10:
    raise SystemExit(f"Selected semantic basis is not orthonormal: {orthogonality}")
patch = semantic["causal_patching"]
selected_mean = float(np.mean([row["selected_different_effect"] for row in patch["rows"]]))
full_mean = float(np.mean([row["full_different_effect"] for row in patch["rows"]]))
if abs(selected_mean - float(patch["selected_mean_effect"])) > 1e-12:
    raise SystemExit("Causal patch selected mean mismatch")
if abs(full_mean - float(patch["full_mean_effect"])) > 1e-12:
    raise SystemExit("Causal patch full mean mismatch")
if not patch["passed"]:
    raise SystemExit("Engineered causal patch did not pass")

receipt = hashlib.sha256(
    json.dumps(
        {
            "causal_checks": checks,
            "orthogonality": round(orthogonality, 15),
            "selected_method": semantic["selected"]["method"],
            "selected_rank": semantic["selected"]["rank"],
            "patch_selected_mean": selected_mean,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
print("SRIC_BLOCK24_INDEPENDENT_VERIFY=PASS")
print(f"verification_receipt={receipt}")
