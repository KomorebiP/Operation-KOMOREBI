from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.audit import run_causal_audit
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.schemas import AuditConfig


def test_preseal_mode_controls_exclude_gold_explicit_cot():
    config = AuditConfig.load("configs/fake_fixture.json")
    result = run_causal_audit(FakeProcedureLatentAdapter(seed=config.seed), make_fixture_records(24), config)
    controls = result["summary"]["mode_controls"]
    assert controls["direct"]["available"] is True
    assert controls["verbalized"]["available"] is False
    assert controls["verbalized"]["reason"] == "reserved_for_post_seal_witness"
    assert controls["verbalized"]["used_before_semantic_seal"] is False
