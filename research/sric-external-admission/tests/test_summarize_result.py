from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("block24_summarize_result", ROOT / "summarize_result.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _fixture_result() -> dict:
    return json.loads((ROOT / "results" / "fake_fixture_block24.json").read_text(encoding="utf-8"))


def test_summary_renders_fixture_calibration_count() -> None:
    text = MODULE.render_summary(_fixture_result())
    assert "Covariance calibration tasks: 8" in text
    assert "Causal admission: **`CONTENT_SPECIFIC`**" in text


def test_summary_handles_disabled_covariance_and_terminal_status() -> None:
    result = copy.deepcopy(_fixture_result())
    result["overall_status"] = "LATENT_UNUSED"
    result["causal_calibration"] = None
    result["causal_admission"]["summary"]["status"] = "LATENT_UNUSED"
    result["semantic_escalation"] = {
        "status": "SEMANTIC_ESCALATION_NOT_ADMISSIBLE",
        "reason": "LATENT_UNUSED",
    }
    text = MODULE.render_summary(result)
    assert "Covariance calibration tasks: disabled / not run" in text
    assert "Overall status: **`LATENT_UNUSED`**" in text
    assert "zero-latent intervention did not meet the frozen necessity gate" in text
