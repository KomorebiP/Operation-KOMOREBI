from __future__ import annotations

import copy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"
if str(REFERENCE) not in sys.path:
    sys.path.insert(0, str(REFERENCE))

from osl_core import OSLError, OSLRuntime, OSLStaticError
from osl_semantic_kernel import verify_semantic_independence


def execute(source: str):
    runtime = OSLRuntime()
    try:
        runtime.run_text(source)
    except (OSLError, OSLStaticError):
        pass
    return runtime.audit_log, runtime.state.snapshot()


def test_unified_semantic_profile_passes_complete_inherited_corpus() -> None:
    verified = 0
    for path in sorted((ROOT / "examples").glob("*.osl")):
        source = path.read_text(encoding="utf-8")
        receipts, final_state = execute(source)
        report = verify_semantic_independence(source, receipts, final_state)
        assert report["all_checks_pass"], (path.name, report["reports"])
        verified += 1
    assert verified == 66


def test_unified_profile_aggregates_component_failure() -> None:
    source = """\
module numeric_mutation
space H dim 2
vector x in H values [1,2]
operator I : H -> H kind linear matrix [[1,0],[0,1]]
apply y = I(x)
"""
    receipts, final_state = execute(source)
    mutated = copy.deepcopy(receipts)
    applied = next(item for item in mutated if item["kind"] == "operator_apply")
    applied["result"]["value"] = [9.0, 9.0]
    report = verify_semantic_independence(source, mutated, final_state)
    assert not report["all_checks_pass"]
    assert report["checks"]["numeric"] is False


def test_unified_profile_fails_closed_on_malformed_input() -> None:
    report = verify_semantic_independence("not valid OSL", [None], {})  # type: ignore[list-item]
    assert not report["all_checks_pass"]
    assert not all(report["checks"].values())


def test_runtime_is_not_imported_by_semantic_component_modules() -> None:
    for path in REFERENCE.glob("osl_semantic_*.py"):
        text = path.read_text(encoding="utf-8")
        assert "from osl_core import" not in text
        assert "import osl_core" not in text
