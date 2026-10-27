import inspect
from sric_real_lrm.adapters.multimode_coconut import CoconutTraceEngine, MultimodeCoconutProntoQAAdapter


def test_real_adapter_is_pinned_to_reviewed_external_commit():
    assert MultimodeCoconutProntoQAAdapter.PINNED_COMMIT == "32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
    assert MultimodeCoconutProntoQAAdapter.CHECKPOINT_FILENAME == "checkpoint_37"
    assert MultimodeCoconutProntoQAAdapter.CHECKPOINT_REVISION == "4ec759a9f9b8a8e7e1a8d1e3e2d43eef969ac83f"
    assert MultimodeCoconutProntoQAAdapter.BASE_MODEL_REVISION == "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def test_trace_engine_exposes_override_contract():
    parameters = inspect.signature(CoconutTraceEngine.run).parameters
    assert "override_trace" in parameters
    assert "labels" in parameters
