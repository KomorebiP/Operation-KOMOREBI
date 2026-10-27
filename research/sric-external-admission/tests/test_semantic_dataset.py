from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.dataset import (
    deterministic_group_split,
    query_polarity_counterfactual,
    validate_polarity_counterfactual,
)
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.schemas import AuditConfig
from sric_real_lrm.semantic import collect_semantic_dataset


def test_query_polarity_counterfactual_flips_only_protected_answer_query():
    record = make_fixture_records(24)[0]
    counterfactual = query_polarity_counterfactual(record)
    validate_polarity_counterfactual(record, counterfactual)
    assert record.answer != counterfactual.answer
    assert record.steps == counterfactual.steps


def test_group_split_is_disjoint_and_complete():
    records = make_fixture_records(48)
    split = deterministic_group_split(
        records,
        seed=7,
        discovery_fraction=0.5,
        calibration_fraction=0.25,
    )
    group_sets = [{record.group_id for record in split[name]} for name in ("discovery", "calibration", "final")]
    assert not (group_sets[0] & group_sets[1])
    assert not (group_sets[0] & group_sets[2])
    assert not (group_sets[1] & group_sets[2])
    assert set().union(*group_sets) == {record.group_id for record in records}


def test_semantic_dataset_excludes_proof_witness_coordinates():
    config = AuditConfig.load("configs/fake_fixture.json")
    records = make_fixture_records(24)
    dataset = collect_semantic_dataset(FakeProcedureLatentAdapter(seed=config.seed), records, config)
    assert dataset.x.shape[0] == len(records) * (config.num_latents - 1)
    assert dataset.future.shape == dataset.x.shape
    assert dataset.intervention.shape == dataset.x.shape
