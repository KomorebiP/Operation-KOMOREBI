from sric_real_lrm.donors import build_same_answer_far_proof_plan, validate_donor_plan
from sric_real_lrm.fixture import make_fixture_records


def test_procedure_donors_match_answer_not_orbit():
    records = make_fixture_records(48)
    plan = build_same_answer_far_proof_plan(records)
    validate_donor_plan(records, plan)
    by_id = {record.task_id: record for record in records}
    assert len(plan) == len(records)
    for item in plan:
        recipient = by_id[item.recipient_id]
        donor = by_id[item.donor_id]
        assert recipient.answer == donor.answer
        assert recipient.orbit_id != donor.orbit_id
