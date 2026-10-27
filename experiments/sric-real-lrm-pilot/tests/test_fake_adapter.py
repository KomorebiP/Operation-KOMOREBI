import numpy as np
from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.fixture import make_fixture_records


def test_fake_adapter_replay_is_exact():
    task = make_fixture_records(24)[0]
    adapter = FakeProcedureLatentAdapter()
    clean = adapter.capture(task)
    replay = adapter.score_with_trace(task, clean.trace)
    assert clean.answer_loss == replay.answer_loss
    assert np.array_equal(clean.answer_logits, replay.answer_logits)
