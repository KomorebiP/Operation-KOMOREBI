from pathlib import Path

from block23.external.preflight import run_preflight

ROOT=Path(__file__).resolve().parents[1]


def test_preflight_fails_closed_without_external_assets():
    result=run_preflight(None,None,ROOT/"frozen"/"SOURCE_LOCK.json")
    assert result["real_checkpoint_executed"] is False
    assert result["status"] == "ADAPTER_VALIDATED_REAL_EXECUTION_BLOCKED"
    assert "checkpoint_missing" in result["blockers"]
