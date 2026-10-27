from sric_real_lrm.donors import build_different_answer_far_proof_plan, validate_donor_plan
from sric_real_lrm.fixture import make_fixture_records


def test_different_answer_donor_plan_is_opposite_answer():
    records = make_fixture_records(48)
    plan = build_different_answer_far_proof_plan(records)
    validate_donor_plan(records, plan, expected_relation="different")
    by_id = {record.task_id: record for record in records}
    assert all(
        by_id[item.recipient_id].answer != by_id[item.donor_id].answer
        for item in plan
    )
