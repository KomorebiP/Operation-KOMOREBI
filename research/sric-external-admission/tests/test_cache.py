from pathlib import Path

import numpy as np

from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.cache import CachedCaptureAdapter
from sric_real_lrm.fixture import make_fixture_records


class CountingFake(FakeProcedureLatentAdapter):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def capture_mode(self, task, mode):
        self.calls += 1
        return super().capture_mode(task, mode)


def test_capture_cache_round_trip(tmp_path: Path):
    wrapped = CountingFake()
    adapter = CachedCaptureAdapter(wrapped, tmp_path)
    task = make_fixture_records(24)[0]
    first = adapter.capture(task)
    second = adapter.capture(task)
    assert wrapped.calls == 1
    assert np.array_equal(first.trace, second.trace)
    assert np.array_equal(first.answer_logits, second.answer_logits)
