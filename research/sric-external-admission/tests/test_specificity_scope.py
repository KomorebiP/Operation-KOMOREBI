from dataclasses import replace

from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.audit import run_causal_audit
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.schemas import AuditConfig


def test_specificity_status_respects_declared_claim_tier():
    base = AuditConfig.load("configs/fake_fixture.json")
    records = make_fixture_records(24)
    content = run_causal_audit(FakeProcedureLatentAdapter(seed=base.seed), records, base)
    assert content["summary"]["status"] == "CONTENT_SPECIFIC"
    procedure_config = replace(base, specificity_claim="procedure", run_covariance_noise=False)
    procedure = run_causal_audit(FakeProcedureLatentAdapter(seed=base.seed), records, procedure_config)
    assert procedure["summary"]["status"] == "PROCEDURE_SPECIFIC"
