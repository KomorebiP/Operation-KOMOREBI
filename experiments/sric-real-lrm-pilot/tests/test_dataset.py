from sric_real_lrm.dataset import semantic_twin, validate_semantic_twin
from sric_real_lrm.fixture import make_fixture_records


def test_semantic_twin_preserves_protected_fields():
    record = make_fixture_records(24)[0]
    twin = semantic_twin(record)
    validate_semantic_twin(record, twin)
    assert twin.question != record.question
    assert twin.proof_signature == record.proof_signature
    assert twin.answer == record.answer
